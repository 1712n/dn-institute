// 🌰 Article analysis using Claude API
export async function analyzeArticle(content, env) {
  const prompt = `You are a cryptocurrency security expert reviewing attack articles. 
Analyze the following article for quality and adherence to submission guidelines.

Focus on:
1. Completeness of attack details
2. Proper categorization
3. Accurate timeline
4. Clear impact assessment
5. References and sources
6. Writing quality and clarity

Article content:
${content}

Return a JSON response with:
{
  "score": <number 0-100>,
  "issues": [
    {
      "severity": "high|medium|low",
      "message": "description of the issue",
      "suggestion": "how to fix it"
    }
  ]
}`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': env.CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-3-haiku-20240307',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
      }),
    });

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.content[0].text;
    
    // 🌰 Parse JSON response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('Invalid response format from Claude');
    }
    
    return JSON.parse(jsonMatch[0]);
  } catch (error) {
    console.error('🌰 Error analyzing article:', error);
    return {
      score: 0,
      issues: [{
        severity: 'high',
        message: 'Failed to analyze article - please check formatting',
        suggestion: 'Ensure article follows markdown format and includes all required sections'
      }]
    };
  }
}