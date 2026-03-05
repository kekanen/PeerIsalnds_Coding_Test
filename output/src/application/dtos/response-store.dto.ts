import { IsNumber, IsDate, IsNotEmpty } from 'class-validator';
import { Type } from 'class-transformer';

/**
 * StoreResponseDto represents the response data transfer object for a store.
 */
export class StoreResponseDto {
  /**
   * Unique identifier for the store.
   */
  @IsNumber()
  storeId: number;

  /**
   * Identifier for the manager staff assigned to the store.
   */
  @IsNumber()
  managerStaffId: number;

  /**
   * Identifier for the address associated with the store.
   */
  @IsNumber()
  addressId: number;

  /**
   * The last update timestamp for the store record.
   */
  @IsDate()
  @Type(() => Date)
  lastUpdate: Date;
}