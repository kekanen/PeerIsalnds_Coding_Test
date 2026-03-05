/**
 * Rental entity interface representing the structure of a rental record.
 */
export interface Rental {
    rentalId: number;
    rentalDate: Date;
    inventoryId: number;
    customerId: number;
    returnDate?: Date;
    staffId: number;
    lastUpdate: Date;
}

/**
 * RentalRepository interface defining the contract for rental data access.
 */
export interface RentalRepository {
    /**
     * Finds a rental by its ID.
     * @param rentalId - The ID of the rental to find.
     * @returns A promise that resolves to the found rental or null if not found.
     */
    findById(rentalId: number): Promise<Rental | null>;

    /**
     * Finds all rentals.
     * @returns A promise that resolves to an array of rentals.
     */
    findAll(): Promise<Rental[]>;

    /**
     * Saves a new rental.
     * @param rental - The rental to save.
     * @returns A promise that resolves to the saved rental.
     */
    save(rental: Rental): Promise<Rental>;

    /**
     * Updates an existing rental.
     * @param rental - The rental to update.
     * @returns A promise that resolves to the updated rental.
     */
    update(rental: Rental): Promise<Rental>;

    /**
     * Deletes a rental by its ID.
     * @param rentalId - The ID of the rental to delete.
     * @returns A promise that resolves when the rental is deleted.
     */
    delete(rentalId: number): Promise<void>;

    /**
     * Finds rentals by customer ID.
     * @param customerId - The ID of the customer whose rentals to find.
     * @returns A promise that resolves to an array of rentals for the specified customer.
     */
    findByCustomerId(customerId: number): Promise<Rental[]>;

    /**
     * Finds rentals by inventory ID.
     * @param inventoryId - The ID of the inventory item whose rentals to find.
     * @returns A promise that resolves to an array of rentals for the specified inventory item.
     */
    findByInventoryId(inventoryId: number): Promise<Rental[]>;

    /**
     * Finds rentals by staff ID.
     * @param staffId - The ID of the staff member whose rentals to find.
     * @returns A promise that resolves to an array of rentals processed by the specified staff member.
     */
    findByStaffId(staffId: number): Promise<Rental[]>;

    /**
     * Finds rentals that are currently active (not returned).
     * @returns A promise that resolves to an array of active rentals.
     */
    findActiveRentals(): Promise<Rental[]>;
}