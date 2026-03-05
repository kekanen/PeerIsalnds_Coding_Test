/**
 * Interface representing the Customer repository.
 * This interface defines the methods for managing Customer entities.
 */
export interface ICustomerRepository<T> {
  /**
   * Finds a customer by their unique identifier.
   * @param customerId - The unique identifier of the customer.
   * @returns A promise that resolves to the customer entity or null if not found.
   */
  findById(customerId: number): Promise<T | null>;

  /**
   * Retrieves all customers.
   * @returns A promise that resolves to an array of customer entities.
   */
  findAll(): Promise<T[]>;

  /**
   * Saves a new customer entity.
   * @param customer - The customer entity to save.
   * @returns A promise that resolves to the saved customer entity.
   */
  save(customer: T): Promise<T>;

  /**
   * Updates an existing customer entity.
   * @param customer - The customer entity with updated values.
   * @returns A promise that resolves to the updated customer entity.
   */
  update(customer: T): Promise<T>;

  /**
   * Deletes a customer by their unique identifier.
   * @param customerId - The unique identifier of the customer to delete.
   * @returns A promise that resolves to a boolean indicating success or failure.
   */
  delete(customerId: number): Promise<boolean>;

  /**
   * Finds customers by their active status.
   * @param isActive - The active status to filter customers.
   * @returns A promise that resolves to an array of customer entities matching the active status.
   */
  findByActiveStatus(isActive: boolean): Promise<T[]>;

  /**
   * Finds customers by their store identifier.
   * @param storeId - The identifier of the store to filter customers.
   * @returns A promise that resolves to an array of customer entities associated with the store.
   */
  findByStoreId(storeId: number): Promise<T[]>;

  /**
   * Finds customers by their email address.
   * @param email - The email address to search for.
   * @returns A promise that resolves to the customer entity or null if not found.
   */
  findByEmail(email: string): Promise<T | null>;
}