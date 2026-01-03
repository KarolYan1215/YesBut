/**
 * API Proxy Route Handler
 */

import type { NextRequest } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8002';

async function proxyRequest(
  request: NextRequest,
  params: { proxy: string[] },
  method: string
): Promise<Response> {
  const path = params.proxy.join('/');
  const url = new URL(`/api/v1/${path}`, BACKEND_URL);

  // Forward query params
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.set(key, value);
  });

  const headers = new Headers();
  request.headers.forEach((value, key) => {
    if (!['host', 'connection'].includes(key.toLowerCase())) {
      headers.set(key, value);
    }
  });

  const fetchOptions: RequestInit = {
    method,
    headers,
  };

  if (['POST', 'PUT', 'PATCH'].includes(method)) {
    const contentType = request.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      fetchOptions.body = await request.text();
    }
  }

  try {
    const response = await fetch(url.toString(), fetchOptions);

    // Handle SSE streaming
    if (response.headers.get('content-type')?.includes('text/event-stream')) {
      return new Response(response.body, {
        status: response.status,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }

    const data = await response.text();
    return new Response(data, {
      status: response.status,
      headers: { 'Content-Type': response.headers.get('content-type') || 'application/json' },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Backend unavailable' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

export async function GET(
  request: NextRequest,
  context: { params: { proxy: string[] } }
): Promise<Response> {
  return proxyRequest(request, context.params, 'GET');
}

export async function POST(
  request: NextRequest,
  context: { params: { proxy: string[] } }
): Promise<Response> {
  return proxyRequest(request, context.params, 'POST');
}

export async function PUT(
  request: NextRequest,
  context: { params: { proxy: string[] } }
): Promise<Response> {
  return proxyRequest(request, context.params, 'PUT');
}

export async function DELETE(
  request: NextRequest,
  context: { params: { proxy: string[] } }
): Promise<Response> {
  return proxyRequest(request, context.params, 'DELETE');
}

export async function PATCH(
  request: NextRequest,
  context: { params: { proxy: string[] } }
): Promise<Response> {
  return proxyRequest(request, context.params, 'PATCH');
}
