export enum ActionType {
  WRITE = 'write_letter',
  REPLY = 'reply_letter',
}

export interface RewardItem {
  name: string;
  description: string;
  category: string;
}

export interface RewardItemDetail extends RewardItem {
  id: string;
}
