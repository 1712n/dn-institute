export type ArticleCheckJob = {
  delivery_id: string;
  repo_full_name: string;
  pr_number: number;
  comment_id: number;
  actor: string;
  installation_id: number;
};

