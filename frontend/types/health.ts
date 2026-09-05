export interface HealthStatus {
  api: "ok";
  database: "connected" | "unreachable";
  environment: string;
}
