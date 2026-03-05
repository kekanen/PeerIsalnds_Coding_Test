import { IsNotEmpty, IsOptional, IsPositive, IsDate } from 'class-validator';

/**
 * UpdateRentalDto is used for updating rental information.
 */
export class UpdateRentalDto {
  /**
   * The unique identifier for the rental.
   * @optional
   */
  @IsOptional()
  @IsPositive()
  rentalId?: number;

  /**
   * The date when the rental was made.
   * @required
   */
  @IsNotEmpty()
  @IsDate()
  rentalDate: Date;

  /**
   * The unique identifier for the inventory item being rented.
   * @optional
   */
  @IsOptional()
  @IsPositive()
  inventoryId?: number;

  /**
   * The unique identifier for the customer renting the item.
   * @optional
   */
  @IsOptional()
  @IsPositive()
  customerId?: number;

  /**
   * The date when the rental item is returned.
   * @optional
   */
  @IsOptional()
  @IsDate()
  returnDate?: Date;

  /**
   * The unique identifier for the staff member processing the rental.
   * @optional
   */
  @IsOptional()
  @IsPositive()
  staffId?: number;

  /**
   * The date when the rental was last updated.
   * @optional
   */
  @IsOptional()
  @IsDate()
  lastUpdate?: Date;
}