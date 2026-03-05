import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  OneToMany,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';
import { IsNotEmpty, IsOptional } from 'class-validator';
import { Inventory } from './Inventory';
import { Customer } from './Customer';
import { Staff } from './Staff';
import { Payment } from './Payment';

/**
 * Represents a rental transaction in the rental management system.
 * 
 * Business Rules:
 * - Rental date must not be null.
 * - Only active customers can create rentals.
 * - Inventory item must be available (no open rental) before renting.
 * - Staff member must be from the same store as the inventory item.
 */
@Entity()
export class Rental {
  @PrimaryGeneratedColumn()
  rentalId!: number;

  @Column({ type: 'timestamp', nullable: false })
  @IsNotEmpty()
  rentalDate!: Date;

  @Column({ type: 'int', nullable: false })
  @IsNotEmpty()
  inventoryId!: number;

  @Column({ type: 'int', nullable: false })
  @IsNotEmpty()
  customerId!: number;

  @Column({ type: 'timestamp', nullable: true })
  @IsOptional()
  returnDate?: Date;

  @Column({ type: 'int', nullable: false })
  @IsNotEmpty()
  staffId!: number;

  @UpdateDateColumn({ type: 'timestamp' })
  lastUpdate!: Date;

  @CreateDateColumn({ type: 'timestamp' })
  createdAt!: Date;

  @ManyToOne(() => Inventory, (inventory) => inventory.rentals)
  inventory!: Inventory;

  @ManyToOne(() => Customer, (customer) => customer.rentals)
  customer!: Customer;

  @ManyToOne(() => Staff, (staff) => staff.rentals)
  staff!: Staff;

  @OneToMany(() => Payment, (payment) => payment.rental)
  payments!: Payment[];
}