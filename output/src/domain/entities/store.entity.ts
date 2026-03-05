import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  OneToMany,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';
import { IsNotEmpty, IsPositive } from 'class-validator';
import { Staff } from './Staff';
import { Address } from './Address';
import { Inventory } from './Inventory';
import { Customer } from './Customer';

/**
 * Represents a Store entity in the system.
 * 
 * Business Rules:
 * - Each store must have exactly one manager.
 * - Manager must be a staff member assigned to that store.
 * - Store ID must not be null in inventory records.
 */
@Entity()
export class Store {
  @PrimaryGeneratedColumn()
  storeId!: number;

  @Column({ unique: true })
  @IsNotEmpty()
  @IsPositive()
  managerStaffId!: number;

  @Column()
  @IsNotEmpty()
  @IsPositive()
  addressId!: number;

  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP', onUpdate: 'CURRENT_TIMESTAMP' })
  lastUpdate!: Date;

  @CreateDateColumn({ type: 'timestamp' })
  createdAt!: Date;

  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt!: Date;

  @ManyToOne(() => Staff, (staff) => staff.stores)
  manager!: Staff;

  @ManyToOne(() => Address, (address) => address.stores)
  address!: Address;

  @OneToMany(() => Inventory, (inventory) => inventory.store)
  inventories!: Inventory[];

  @OneToMany(() => Customer, (customer) => customer.store)
  customers!: Customer[];
}