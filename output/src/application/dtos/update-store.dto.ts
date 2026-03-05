import { IsNumber, IsOptional, IsPositive } from 'class-validator';

/**
 * DTO for updating store information.
 */
export class UpdateStoreDto {
  /**
   * Unique identifier for the store.
   * @type {number}
   */
  @IsOptional()
  @IsNumber()
  @IsPositive()
  storeId?: number;

  /**
   * Unique identifier for the manager staff member.
   * @type {number}
   */
  @IsOptional()
  @IsNumber()
  @IsPositive()
  managerStaffId?: number;

  /**
   * Unique identifier for the address associated with the store.
   * @type {number}
   */
  @IsOptional()
  @IsNumber()
  @IsPositive()
  addressId?: number;
}