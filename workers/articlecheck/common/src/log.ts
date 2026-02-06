export type LogLevel = "debug" | "info" | "warn" | "error";

export type LogRecord = {
  level: LogLevel;
  msg: string;
  at: string;
  [key: string]: unknown;
};

export function log(level: LogLevel, msg: string, fields: Record<string, unknown> = {}): void {
  const rec: LogRecord = {
    level,
    msg,
    at: new Date().toISOString(),
    ...fields
  };
  // Cloudflare Logs is line-oriented; JSON keeps it grep-friendly and structured.
  console.log(JSON.stringify(rec));
}

export const logger = {
  debug: (msg: string, fields?: Record<string, unknown>) => log("debug", msg, fields),
  info: (msg: string, fields?: Record<string, unknown>) => log("info", msg, fields),
  warn: (msg: string, fields?: Record<string, unknown>) => log("warn", msg, fields),
  error: (msg: string, fields?: Record<string, unknown>) => log("error", msg, fields)
};

