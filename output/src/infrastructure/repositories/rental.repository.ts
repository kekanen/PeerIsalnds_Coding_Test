import { EntityRepository, Repository, getRepository } from 'typeorm';
import { Rental } from './Rental'; // Assuming Rental is an entity class
import { RentalRepository } from './RentalRepository'; // Assuming RentalRepository is the interface
import { Injectable } from '@nestjs/common';
import { Logger } from '@nestjs/common';

@Injectable()
@EntityRepository(Rental)
export class RentalRepositoryImpl extends Repository<Rental> implements RentalRepository {
    private readonly logger = new Logger(RentalRepositoryImpl.name);

    /**
     * Finds a rental by its ID.
     * @param rentalId - The ID of the rental to find.
     * @returns A promise that resolves to the found rental or null if not found.
     */
    async findById(rentalId: number): Promise<Rental | null> {
        try {
            const rental = await this.findOne(rentalId);
            this.logger.log(`Found rental with ID: ${rentalId}`);
            return rental || null;
        } catch (error) {
            this.logger.error(`Error finding rental with ID: ${rentalId}`, error);
            throw error;
        }
    }

    /**
     * Finds all rentals.
     * @returns A promise that resolves to an array of rentals.
     */
    async findAll(): Promise<Rental[]> {
        try {
            const rentals = await this.find();
            this.logger.log(`Retrieved all rentals, count: ${rentals.length}`);
            return rentals;
        } catch (error) {
            this.logger.error('Error retrieving all rentals', error);
            throw error;
        }
    }

    /**
     * Saves a new rental.
     * @param rental - The rental to save.
     * @returns A promise that resolves to the saved rental.
     */
    async save(rental: Rental): Promise<Rental> {
        try {
            const savedRental = await this.save(rental);
            this.logger.log(`Saved rental with ID: ${savedRental.rentalId}`);
            return savedRental;
        } catch (error) {
            this.logger.error('Error saving rental', error);
            throw error;
        }
    }

    /**
     * Updates an existing rental.
     * @param rental - The rental to update.
     * @returns A promise that resolves to the updated rental.
     */
    async update(rental: Rental): Promise<Rental> {
        try {
            await this.save(rental);
            this.logger.log(`Updated rental with ID: ${rental.rentalId}`);
            return rental;
        } catch (error) {
            this.logger.error('Error updating rental', error);
            throw error;
        }
    }

    /**
     * Deletes a rental by its ID.
     * @param rentalId - The ID of the rental to delete.
     * @returns A promise that resolves when the rental is deleted.
     */
    async delete(rentalId: number): Promise<void> {
        try {
            await this.delete(rentalId);
            this.logger.log(`Deleted rental with ID: ${rentalId}`);
        } catch (error) {
            this.logger.error(`Error deleting rental with ID: ${rentalId}`, error);
            throw error;
        }
    }

    /**
     * Finds rentals by customer ID.
     * @param customerId - The ID of the customer whose rentals to find.
     * @returns A promise that resolves to an array of rentals for the specified customer.
     */
    async findByCustomerId(customerId: number): Promise<Rental[]> {
        try {
            const rentals = await this.find({ where: { customerId } });
            this.logger.log(`Found ${rentals.length} rentals for customer ID: ${customerId}`);
            return rentals;
        } catch (error) {
            this.logger.error(`Error finding rentals for customer ID: ${customerId}`, error);
            throw error;
        }
    }

    /**
     * Finds rentals by inventory ID.
     * @param inventoryId - The ID of the inventory item whose rentals to find.
     * @returns A promise that resolves to an array of rentals for the specified inventory item.
     */
    async findByInventoryId(inventoryId: number): Promise<Rental[]> {
        try {
            const rentals = await this.find({ where: { inventoryId } });
            this.logger.log(`Found ${rentals.length} rentals for inventory ID: ${inventoryId}`);
            return rentals;
        } catch (error) {
            this.logger.error(`Error finding rentals for inventory ID: ${inventoryId}`, error);
            throw error;
        }
    }

    /**
     * Finds rentals by staff ID.
     * @param staffId - The ID of the staff member whose rentals to find.
     * @returns A promise that resolves to an array of rentals processed by the specified staff member.
     */
    async findByStaffId(staffId: number): Promise<Rental[]> {
        try {
            const rentals = await this.find({ where: { staffId } });
            this.logger.log(`Found ${rentals.length} rentals for staff ID: ${staffId}`);
            return rentals;
        } catch (error) {
            this.logger.error(`Error finding rentals for staff ID: ${staffId}`, error);
            throw error;
        }
    }

    /**
     * Finds rentals that are currently active (not returned).
     * @returns A promise that resolves to an array of active rentals.
     */
    async findActiveRentals(): Promise<Rental[]> {
        try {
            const rentals = await this.find({ where: { returnDate: null } });
            this.logger.log(`Found ${rentals.length} active rentals`);
            return rentals;
        } catch (error) {
            this.logger.error('Error finding active rentals', error);
            throw error;
        }
    }
}