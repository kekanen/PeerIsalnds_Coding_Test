import { Controller, Get, Post, Put, Delete, Route, Tags, Path, Body, SuccessResponse, Response as SwaggerResponse } from 'tsoa';
import { Request, Response, NextFunction } from 'express';
import { validateOrReject, IsNotEmpty, IsPositive } from 'class-validator';

interface StoreDto {
    storeId?: number;
    managerStaffId: number;
    addressId: number;
}

class StoreRequestDto {
    @IsNotEmpty()
    managerStaffId: number;

    @IsNotEmpty()
    addressId: number;
}

class UpdateStoreRequestDto {
    @IsPositive()
    storeId: number;

    @IsNotEmpty()
    managerStaffId?: number;

    @IsNotEmpty()
    addressId?: number;
}

@Route('stores')
@Tags('Store Management')
export class StoreController extends Controller {
    constructor() {
        super();
    }

    /**
     * Get list of all stores
     * @returns {Promise<StoreDto[]>} List of stores
     */
    @Get()
    public async getStores(req: Request, res: Response, next: NextFunction): Promise<StoreDto[]> {
        try {
            // Logic to retrieve stores from the database
            const stores: StoreDto[] = []; // Replace with actual data retrieval
            return stores;
        } catch (error) {
            next(error);
        }
    }

    /**
     * Add a new store
     * @param {StoreRequestDto} requestBody - Store details
     * @returns {Promise<StoreDto>} Created store
     */
    @Post()
    @SuccessResponse('201', 'Created')
    @SwaggerResponse('400', 'Bad Request')
    public async addStore(@Body() requestBody: StoreRequestDto, req: Request, res: Response, next: NextFunction): Promise<StoreDto> {
        try {
            await validateOrReject(requestBody);
            // Logic to add a new store to the database
            const newStore: StoreDto = { storeId: 1, ...requestBody }; // Replace with actual data insertion
            res.status(201).send(newStore);
            return newStore;
        } catch (error) {
            next(error);
        }
    }

    /**
     * Update store information
     * @param {number} storeId - Store primary key
     * @param {UpdateStoreRequestDto} requestBody - Updated store details
     * @returns {Promise<StoreDto>} Updated store
     */
    @Put('{storeId}')
    @SuccessResponse('200', 'Success')
    @SwaggerResponse('404', 'Store Not Found')
    @SwaggerResponse('403', 'Insufficient Privileges')
    public async updateStore(@Path() storeId: number, @Body() requestBody: UpdateStoreRequestDto, req: Request, res: Response, next: NextFunction): Promise<StoreDto> {
        try {
            await validateOrReject(requestBody);
            // Logic to update store in the database
            const updatedStore: StoreDto = { storeId, ...requestBody }; // Replace with actual data update
            return updatedStore;
        } catch (error) {
            next(error);
        }
    }

    /**
     * Delete a store
     * @param {number} storeId - Store primary key
     * @returns {Promise<void>}
     */
    @Delete('{storeId}')
    @SuccessResponse('204', 'No Content')
    @SwaggerResponse('404', 'Store Not Found')
    @SwaggerResponse('409', 'Store Has Active Inventory')
    public async deleteStore(@Path() storeId: number, req: Request, res: Response, next: NextFunction): Promise<void> {
        try {
            // Logic to delete store from the database
            res.status(204).send();
        } catch (error) {
            next(error);
        }
    }
}