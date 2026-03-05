import { IsNotEmpty, IsOptional, IsPositive, IsDate } from 'class-validator';
import { Type } from 'class-transformer';

/**
 * RentalResponseDto represents the response structure for rental information.
 */
export class RentalResponseDto {
  /**
   * Unique identifier for the rental.
   */
  @IsPositive()
  rentalId: number;

  /**
   * The date when the rental was made.
   */
  @IsNotEmpty()
  @IsDate()
  @Type(() => Date)
  rentalDate: Date;

  /**
   * Identifier for the inventory item being rented.
   */
  @IsNotEmpty()
  @IsPositive()
  inventoryId: number;

  /**
   * Identifier for the customer who rented the item.
   */
  @IsNotEmpty()
  @IsPositive()
  customerId: number;

  /**
   * The date when the rental item is returned.
   */
  @IsOptional()
  @IsDate()
  @Type(() => Date)
  returnDate?: Date;

  /**
   * Identifier for the staff member processing the rental.
   */
  @IsNotEmpty()
  @IsPositive()
  staffId: number;

  /**
   * The date when the rental record was last updated.
   */
  @IsOptional()
  @IsDate()
  @Type(() => Date)
  lastUpdate?: Date;
}