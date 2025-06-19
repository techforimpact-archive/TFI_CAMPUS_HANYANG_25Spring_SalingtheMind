import { BaseResponse } from '../response_dto';
import { ActionType, RewardItem } from '../type/reward.type';

export interface GrantRewardRequestDto {
  action: ActionType;
  content: string;
}

export interface GrantRewardResponseDto extends BaseResponse {
  action: ActionType;
  base_point: number;
  bonus_point: number;
  leveled_up: boolean;
  level: number;
  new_items: RewardItem[];
}

export interface MyRewardResponseDto extends BaseResponse {
  nickname: string;
  point: number;
  level: number;
}
