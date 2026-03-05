import { IsNotEmpty, IsPositive, IsOptional, IsDate } from 'class-validator';
import { Type } from 'class-transformer';

/**
 * DTO for creating a rental record.
 */
export class CreateRentalDto {
  @IsNotEmpty()
  @IsDate()
  @Type(() => Date)
  rentalDate: Date;

  @IsNotEmpty()
  @IsPositive()
  inventoryId: number;

  @IsNotEmpty()
  @IsPositive()
  customerId: number;

  @IsOptional()
  @IsDate()
  @Type(() => Date)
  returnDate?: Date;

  @IsNotEmpty()
  @IsPositive()
  staffId: number;
}