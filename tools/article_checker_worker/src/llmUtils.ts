interface LLMMessage {
    role: 'system' | 'user';
    content: string;
}

interface LLMRequestBody {
    model: string;
    messages: LLMMessage[];
}

interface LLMResponse {
    choices: { message: { content: string } }[];
}

export async function callLLM(
    systemPrompt: string,
    prompt: string,
    LLM_API_KEY: string,
    LLM_ENDPOINT: string,
    model: string = "gpt-3.5-turbo-0125"
): Promise<string> {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${LLM_API_KEY}`
    };

    const requestBody: LLMRequestBody = {
        model,
        messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: prompt }
        ]
    };

    const response = await fetch(LLM_ENDPOINT, { method: 'POST', headers, body: JSON.stringify(requestBody) });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const answer = await response.json() as LLMResponse;

    if (!answer.choices || !answer.choices[0] || !answer.choices[0].message.content) {
        throw new Error('No content in OpenAI response');
    }

    return answer.choices[0].message.content;
}