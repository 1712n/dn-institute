use worker::*;
use serde::{Deserialize, Serialize};
use tokio::task::JoinHandle;
use tokio::time::{sleep, Duration};

#[derive(Debug, Deserialize)]
struct TextEntry {
    text: String,
    namespace: String,
}

#[derive(Debug, Deserialize)]
struct ApiRequestBody {
    data: Vec<TextEntry>,
}

#[derive(Debug, Serialize)]
struct SimilarityScore {
    similarity_score: f64,
    error: Option<String>,
}

#[derive(Debug, Serialize)]
struct ErrorResponse {
    error: String,
}

async fn retry<F, Fut>(mut func: F, retries: usize) -> Result<Fut::Output, String>
where
    F: FnMut() -> Fut,
    Fut: std::future::Future,
{
    for attempt in 0..retries {
        match func().await {
            Ok(result) => return Ok(result),
            Err(error) => {
                if attempt < retries - 1 {
                    unsafe {
                        console_log!("Attempt {} failed: {:?}", attempt + 1, error);
                    }
                    // Exponential backoff
                    let delay_ms = 2_u64.pow(attempt as u32) * 100;
                    sleep(Duration::from_millis(delay_ms)).await;
                } else {
                    return Err(error.to_string());
                }
            }
        }
    }
    Err("Exhausted all retries".to_string())
}

async fn get_model_response(text: &str, env: &Env) -> Result<f64, String> {
    // Assuming `AI.run` and `VECTORIZE_INDEX.query` are Cloudflare Worker AI functions
    let model_resp = retry(
        || env.AI.run("@cf/baai/bge-base-en-v1.5", json!({ "text": [text] })),
        env.RETRY_LIMIT as usize,
    )
    .await?;

    let vector = match model_resp.get("data").and_then(|data| data.as_array()).and_then(|data| data.get(0)) {
        Some(value) => match value.as_f64() {
            Some(f) => f,
            None => return Err("Invalid model response format".to_string()),
        },
        None => return Err("Invalid model response format".to_string()),
    };

    let search_response = retry(
        || env.VECTORIZE_INDEX.query(*vector, json!({ "namespace": "default", "topK": 1 })),
        env.RETRY_LIMIT as usize,
    )
    .await?;

    let similarity_score = match search_response.get("matches").and_then(|matches| matches.as_array()).and_then(|matches| matches.get(0)) {
        Some(match_item) => match match_item.get("score").and_then(|score| score.as_f64()) {
            Some(score) => score,
            None => 0.0, // Default similarity score
        },
        None => 0.0, // Default similarity score
    };

    Ok(similarity_score)
}

async fn process_batch(entries: Vec<TextEntry>, env: Env) -> Vec<SimilarityScore> {
    let mut similarity_scores = Vec::new();
    let mut handles = Vec::new();

    for entry in entries {
        let env = env.clone();
        let handle: JoinHandle<Option<SimilarityScore>> = tokio::spawn(async move {
            match get_model_response(&entry.text, &env).await {
                Ok(similarity_score) => Some(SimilarityScore {
                    similarity_score,
                    error: None,
                }),
                Err(error) => Some(SimilarityScore {
                    similarity_score: 0.0,
                    error: Some(error),
                }),
            }
        });

        handles.push(handle);
    }

    for handle in handles {
        if let Some(result) = handle.await.unwrap() {
            similarity_scores.push(result);
        }
    }

    similarity_scores
}

#[event(fetch)]
pub async fn main(req: Request, env: Env, _ctx: worker::Context) -> Result<Response> {
    if !matches!(req.method(), Method::Post) {
        return Response::error("Method Not Allowed", 405);
    }

    let api_request_body: ApiRequestBody = match req.json().await {
        Ok(body) => body,
        Err(_) => return Response::error("Invalid JSON format", 400),
    };

    let batch_process_limit = env.BATCH_PROCESS_LIMIT as usize;
    let batches: Vec<Vec<TextEntry>> = api_request_body.data.chunks(batch_process_limit).map(|chunk| chunk.to_vec()).collect();

    let mut batch_results = Vec::new();
    for batch in batches {
        batch_results.push(process_batch(batch, env.clone()).await);
    }

    let response_body: Vec<SimilarityScore> = batch_results.into_iter().flatten().collect();

    Response::ok_with_json(&response_body)
}
