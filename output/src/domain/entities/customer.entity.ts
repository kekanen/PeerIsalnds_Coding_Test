import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  OneToMany,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';
import { IsNotEmpty, IsString, IsEmail, MaxLength, IsBoolean } from 'class-validator';
import { Store } from './Store';
import { Address } from './Address';
import { Rental } from './Rental';
import { Payment } from './Payment';

/**
 * Represents a customer in the system.
 * 
 * Business Rules:
 * - Only active customers may rent DVDs.
 * - Email must be unique across all customers.
 * - Customer must belong to exactly one store.
 */
@Entity()
export class Customer {
  @PrimaryGeneratedColumn()
  customerId!: number;

  @Column()
  @IsNotEmpty()
  storeId!: number;

  @Column()
  @IsNotEmpty()
  @IsString()
  @MaxLength(45)
  firstName!: string;

  @Column()
  @IsNotEmpty()
  @IsString()
  @MaxLength(45)
  lastName!: string;

  @Column({ nullable: true })
  @IsEmail()
  @MaxLength(50)
  email?: string;

  @Column()
  @IsNotEmpty()
  addressId!: number;

  @Column({ default: true })
  @IsBoolean()
  active!: boolean;

  @CreateDateColumn()
  createDate!: Date;

  @UpdateDateColumn()
  lastUpdate!: Date;

  @ManyToOne(() => Store, (store) => store.customers)
  store!: Store;

  @ManyToOne(() => Address, (address) => address.customers)
  address!: Address;

  @OneToMany(() => Rental, (rental) => rental.customer)
  rentals!: Rental[];

  @OneToMany(() => Payment, (payment) => payment.customer)
  payments!: Payment[];
}