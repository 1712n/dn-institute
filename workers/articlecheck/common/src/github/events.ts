export type IssueCommentCreatedEvent = {
  action: "created";
  issue: {
    number: number;
    pull_request?: unknown;
  };
  comment: {
    id: number;
    body: string;
  };
  repository: {
    full_name: string;
  };
  sender: {
    login: string;
  };
  installation?: {
    id: number;
  };
};

