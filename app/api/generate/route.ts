import { NextResponse } from 'next/server';
import OpenAI from 'openai';

// Initialize the OpenAI client pointing to GitHub Models
const client = new OpenAI({
  baseURL: 'https://models.inference.ai.azure.com',
  apiKey: process.env.GITHUB_TOKEN || '',
});

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { issue } = body;

    if (!issue || typeof issue !== 'string') {
      return NextResponse.json({ error: 'Issue is required' }, { status: 400 });
    }

    const response = await client.chat.completions.create({
      model: 'gpt-4o', 
      messages: [
        { 
          role: 'system', 
          content: 'You are a senior software engineer covering up for a bug. The user will give you a simple bug or delay. Generate a highly technical, slightly absurd, but plausible-sounding excuse to tell the product manager. Keep it under 2 sentences.' 
        },
        { 
          role: 'user', 
          content: `The issue is: ${issue}` 
        }
      ],
      temperature: 0.8,
    });

    const excuse = response.choices[0]?.message?.content;

    if (!excuse) {
      throw new Error("Failed to generate an excuse. The response was empty.");
    }

    return NextResponse.json({ result: excuse });

  } catch (error: any) {
    console.error("GitHub Models Error:", error);
    return NextResponse.json(
      { error: 'Failed to generate response. Rate limit may be reached.' }, 
      { status: 500 }
    );
  }
}