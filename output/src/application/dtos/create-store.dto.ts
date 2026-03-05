import { IsNotEmpty, IsPositive, IsDate, IsOptional } from 'class-validator';
import { Type } from 'class-transformer';

/**
 * DTO for creating a new store.
 */
export class CreateStoreDto {
  /**
   * The ID of the manager staff member assigned to the store.
   * Must be a positive number and unique.
   */
  @IsNotEmpty()
  @IsPositive()
  managerStaffId: number;

  /**
   * The ID of the address associated with the store.
   * Must be a positive number.
   */
  @IsNotEmpty()
  @IsPositive()
  addressId: number;

  /**
   * The date when the store was last updated.
   * This field is auto-updated and not required during creation.
   */
  @IsOptional()
  @IsDate()
  @Type(() => Date)
  lastUpdate?: Date;
}