import { EntityRepository, Repository, getRepository } from 'typeorm';
import { Store } from '../entities/Store'; // Adjust the import path as necessary
import { IStoreRepository } from './IStoreRepository'; // Adjust the import path as necessary
import { Logger } from '../utils/Logger'; // Adjust the import path as necessary

@EntityRepository(Store)
export class StoreRepository extends Repository<Store> implements IStoreRepository<Store> {
  private logger = new Logger('StoreRepository');

  /**
   * Finds a store by its ID.
   * @param storeId - The ID of the store to find.
   * @returns A promise that resolves to the store entity or null if not found.
   */
  async findById(storeId: number): Promise<Store | null> {
    try {
      this.logger.log(`Finding store with ID: ${storeId}`);
      return await this.findOne(storeId) || null;
    } catch (error) {
      this.logger.error(`Error finding store with ID: ${storeId}`, error);
      throw error;
    }
  }

  /**
   * Finds all stores.
   * @returns A promise that resolves to an array of store entities.
   */
  async findAll(): Promise<Store[]> {
    try {
      this.logger.log('Finding all stores');
      return await this.find();
    } catch (error) {
      this.logger.error('Error finding all stores', error);
      throw error;
    }
  }

  /**
   * Saves a new store entity.
   * @param store - The store entity to save.
   * @returns A promise that resolves to the saved store entity.
   */
  async save(store: Store): Promise<Store> {
    try {
      this.logger.log('Saving store', store);
      return await this.save(store);
    } catch (error) {
      this.logger.error('Error saving store', error);
      throw error;
    }
  }

  /**
   * Updates an existing store entity.
   * @param store - The store entity with updated values.
   * @returns A promise that resolves to the updated store entity.
   */
  async update(store: Store): Promise<Store> {
    try {
      this.logger.log('Updating store', store);
      return await this.save(store);
    } catch (error) {
      this.logger.error('Error updating store', error);
      throw error;
    }
  }

  /**
   * Deletes a store by its ID.
   * @param storeId - The ID of the store to delete.
   * @returns A promise that resolves to a boolean indicating success or failure.
   */
  async delete(storeId: number): Promise<boolean> {
    try {
      this.logger.log(`Deleting store with ID: ${storeId}`);
      const result = await this.delete(storeId);
      return result.affected !== 0;
    } catch (error) {
      this.logger.error(`Error deleting store with ID: ${storeId}`, error);
      throw error;
    }
  }

  /**
   * Finds stores by manager staff ID.
   * @param managerStaffId - The ID of the manager staff.
   * @returns A promise that resolves to an array of store entities managed by the specified staff.
   */
  async findByManagerStaffId(managerStaffId: number): Promise<Store[]> {
    try {
      this.logger.log(`Finding stores managed by staff ID: ${managerStaffId}`);
      return await this.createQueryBuilder('store')
        .where('store.managerStaffId = :managerStaffId', { managerStaffId })
        .getMany();
    } catch (error) {
      this.logger.error(`Error finding stores by manager staff ID: ${managerStaffId}`, error);
      throw error;
    }
  }

  /**
   * Finds stores by address ID.
   * @param addressId - The ID of the address.
   * @returns A promise that resolves to an array of store entities located at the specified address.
   */
  async findByAddressId(addressId: number): Promise<Store[]> {
    try {
      this.logger.log(`Finding stores by address ID: ${addressId}`);
      return await this.createQueryBuilder('store')
        .where('store.addressId = :addressId', { addressId })
        .getMany();
    } catch (error) {
      this.logger.error(`Error finding stores by address ID: ${addressId}`, error);
      throw error;
    }
  }

  /**
   * Finds stores updated after a specific date.
   * @param lastUpdate - The date to compare against.
   * @returns A promise that resolves to an array of store entities updated after the specified date.
   */
  async findUpdatedAfter(lastUpdate: Date): Promise<Store[]> {
    try {
      this.logger.log(`Finding stores updated after: ${lastUpdate}`);
      return await this.createQueryBuilder('store')
        .where('store.lastUpdate > :lastUpdate', { lastUpdate })
        .getMany();
    } catch (error) {
      this.logger.error(`Error finding stores updated after: ${lastUpdate}`, error);
      throw error;
    }
  }
}