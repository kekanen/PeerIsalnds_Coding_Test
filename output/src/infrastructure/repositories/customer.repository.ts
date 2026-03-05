import { EntityRepository, Repository, getRepository } from 'typeorm';
import { Customer } from '../entities/Customer'; // Adjust the import path as necessary
import { ICustomerRepository } from './ICustomerRepository'; // Adjust the import path as necessary
import { Injectable } from '@nestjs/common';

@Injectable()
@EntityRepository(Customer)
export class CustomerRepository extends Repository<Customer> implements ICustomerRepository<Customer> {
  
  /**
   * Finds a customer by their unique identifier.
   * @param customerId - The unique identifier of the customer.
   * @returns A promise that resolves to the customer entity or null if not found.
   */
  async findById(customerId: number): Promise<Customer | null> {
    try {
      return await this.findOne(customerId);
    } catch (error) {
      console.error(`Error finding customer by ID: ${customerId}`, error);
      throw new Error('Could not find customer');
    }
  }

  /**
   * Retrieves all customers.
   * @returns A promise that resolves to an array of customer entities.
   */
  async findAll(): Promise<Customer[]> {
    try {
      return await this.find();
    } catch (error) {
      console.error('Error retrieving all customers', error);
      throw new Error('Could not retrieve customers');
    }
  }

  /**
   * Saves a new customer entity.
   * @param customer - The customer entity to save.
   * @returns A promise that resolves to the saved customer entity.
   */
  async save(customer: Customer): Promise<Customer> {
    try {
      const savedCustomer = await this.save(customer);
      console.log(`Customer saved: ${savedCustomer.id}`);
      return savedCustomer;
    } catch (error) {
      console.error('Error saving customer', error);
      throw new Error('Could not save customer');
    }
  }

  /**
   * Updates an existing customer entity.
   * @param customer - The customer entity with updated values.
   * @returns A promise that resolves to the updated customer entity.
   */
  async update(customer: Customer): Promise<Customer> {
    try {
      await this.save(customer);
      console.log(`Customer updated: ${customer.id}`);
      return customer;
    } catch (error) {
      console.error('Error updating customer', error);
      throw new Error('Could not update customer');
    }
  }

  /**
   * Deletes a customer by their unique identifier.
   * @param customerId - The unique identifier of the customer to delete.
   * @returns A promise that resolves to a boolean indicating success or failure.
   */
  async delete(customerId: number): Promise<boolean> {
    try {
      const result = await this.delete(customerId);
      console.log(`Customer deleted: ${customerId}`);
      return result.affected > 0;
    } catch (error) {
      console.error('Error deleting customer', error);
      throw new Error('Could not delete customer');
    }
  }

  /**
   * Finds customers by their active status.
   * @param isActive - The active status to filter customers.
   * @returns A promise that resolves to an array of customer entities matching the active status.
   */
  async findByActiveStatus(isActive: boolean): Promise<Customer[]> {
    try {
      return await this.find({ where: { isActive } });
    } catch (error) {
      console.error('Error finding customers by active status', error);
      throw new Error('Could not find customers by active status');
    }
  }

  /**
   * Finds customers by their store identifier.
   * @param storeId - The identifier of the store to filter customers.
   * @returns A promise that resolves to an array of customer entities associated with the store.
   */
  async findByStoreId(storeId: number): Promise<Customer[]> {
    try {
      return await this.find({ where: { storeId } });
    } catch (error) {
      console.error('Error finding customers by store ID', error);
      throw new Error('Could not find customers by store ID');
    }
  }

  /**
   * Finds customers by their email address.
   * @param email - The email address to search for.
   * @returns A promise that resolves to the customer entity or null if not found.
   */
  async findByEmail(email: string): Promise<Customer | null> {
    try {
      return await this.findOne({ where: { email } });
    } catch (error) {
      console.error(`Error finding customer by email: ${email}`, error);
      throw new Error('Could not find customer by email');
    }
  }
}