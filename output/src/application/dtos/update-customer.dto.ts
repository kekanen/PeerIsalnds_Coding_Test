import { IsString, IsNotEmpty, IsOptional, IsBoolean, IsInt, MaxLength, IsDate, IsPositive } from 'class-validator';
import { Type } from 'class-transformer';

/**
 * DTO for updating customer information.
 */
export class UpdateCustomerDto {
  @IsOptional()
  @IsInt()
  @IsPositive()
  storeId?: number;

  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(45)
  firstName?: string;

  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(45)
  lastName?: string;

  @IsOptional()
  @IsString()
  @MaxLength(50)
  email?: string;

  @IsOptional()
  @IsInt()
  @IsPositive()
  addressId?: number;

  @IsOptional()
  @IsBoolean()
  active?: boolean;

  @IsOptional()
  @IsDate()
  @Type(() => Date)
  createDate?: Date;

  @IsOptional()
  @IsDate()
  @Type(() => Date)
  lastUpdate?: Date;
}