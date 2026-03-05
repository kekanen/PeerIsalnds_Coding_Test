/**
 * Interface representing the repository for the Store entity.
 * This interface defines the standard CRUD operations and custom query methods.
 */
export interface IStoreRepository<T> {
  /**
   * Finds a store by its ID.
   * @param storeId - The ID of the store to find.
   * @returns A promise that resolves to the store entity or null if not found.
   */
  findById(storeId: number): Promise<T | null>;

  /**
   * Finds all stores.
   * @returns A promise that resolves to an array of store entities.
   */
  findAll(): Promise<T[]>;

  /**
   * Saves a new store entity.
   * @param store - The store entity to save.
   * @returns A promise that resolves to the saved store entity.
   */
  save(store: T): Promise<T>;

  /**
   * Updates an existing store entity.
   * @param store - The store entity with updated values.
   * @returns A promise that resolves to the updated store entity.
   */
  update(store: T): Promise<T>;

  /**
   * Deletes a store by its ID.
   * @param storeId - The ID of the store to delete.
   * @returns A promise that resolves to a boolean indicating success or failure.
   */
  delete(storeId: number): Promise<boolean>;

  /**
   * Finds stores by manager staff ID.
   * @param managerStaffId - The ID of the manager staff.
   * @returns A promise that resolves to an array of store entities managed by the specified staff.
   */
  findByManagerStaffId(managerStaffId: number): Promise<T[]>;

  /**
   * Finds stores by address ID.
   * @param addressId - The ID of the address.
   * @returns A promise that resolves to an array of store entities located at the specified address.
   */
  findByAddressId(addressId: number): Promise<T[]>;

  /**
   * Finds stores updated after a specific date.
   * @param lastUpdate - The date to compare against.
   * @returns A promise that resolves to an array of store entities updated after the specified date.
   */
  findUpdatedAfter(lastUpdate: Date): Promise<T[]>;
}