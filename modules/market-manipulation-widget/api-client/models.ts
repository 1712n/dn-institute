interface DictionaryRequest {
    marketvenueid?: string | null;
    pairid?: string | null;
    limit?: number | null;
    page?: number | null;
}

interface DictionaryResponse {
    marketvenueid: string
    pairid: string
    type: string
    starttime?: string | null
    active?: boolean | null
}

interface MetricsRequest {
    marketvenueid: string;
    pairid: string;
    start?: string | null;
    end?: string | null;
    sort: 'asc' | 'desc';
    limit?: number | null;
    page?: number | null;
}

interface TimeOfTrade {
    seconds: number[]
}

interface MetricsResponse {
    timestamp: string;
    marketvenue: string;
    pairid: string;
    vwap: number;
    tradecount: number;
    timeoftrade: TimeOfTrade;
    buysellratio: number;
    buysellratioabs: number;
    firstdigitdist: Record<string, number>[]
    benfordlawtest: number;
    volumedist: number[][];
}

interface ApiError {
    error: string;
}

export {DictionaryRequest, DictionaryResponse, MetricsRequest, MetricsResponse, ApiError};
