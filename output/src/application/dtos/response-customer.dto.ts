import { IsNumber, IsString, IsNotEmpty, IsOptional, IsBoolean, IsDate, MaxLength } from 'class-validator';
import { Type } from 'class-transformer';

/**
 * CustomerResponseDto represents the response data transfer object for a customer.
 */
export class CustomerResponseDto {
  @IsNumber()
  customerId: number;

  @IsNumber()
  storeId: number;

  @IsString()
  @IsNotEmpty()
  @MaxLength(45)
  firstName: string;

  @IsString()
  @IsNotEmpty()
  @MaxLength(45)
  lastName: string;

  @IsString()
  @IsOptional()
  @MaxLength(50)
  email?: string;

  @IsNumber()
  addressId: number;

  @IsBoolean()
  active: boolean;

  @IsDate()
  @Type(() => Date)
  createDate: Date;

  @IsDate()
  @Type(() => Date)
  lastUpdate: Date;
}