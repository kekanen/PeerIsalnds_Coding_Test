import { IsNotEmpty, IsString, IsEmail, IsPositive, IsBoolean, IsDate, MaxLength } from 'class-validator';

/**
 * DTO for creating a new customer.
 */
export class CreateCustomerDto {
  @IsPositive()
  storeId: number;

  @IsNotEmpty()
  @IsString()
  @MaxLength(45)
  firstName: string;

  @IsNotEmpty()
  @IsString()
  @MaxLength(45)
  lastName: string;

  @IsOptional()
  @IsEmail()
  @MaxLength(50)
  email?: string;

  @IsPositive()
  addressId: number;

  @IsBoolean()
  active: boolean;

  @IsDate()
  createDate: Date;

  // lastUpdate is not included as it is auto-updated
}