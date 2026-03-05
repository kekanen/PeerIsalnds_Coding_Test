import { Controller, Get, Post, Put, Delete, Route, Tags, Path, Body, Query, SuccessResponse, Response as SwaggerResponse } from 'tsoa';
import { Request, Response, NextFunction } from 'express';
import { validateOrReject } from 'class-validator';

interface CustomerDto {
    customerId?: number;
    storeId: number;
    firstName: string;
    lastName: string;
    email: string;
    addressId: number;
    active?: boolean;
}

@Route('customers')
@Tags('Customer')
export class CustomerController extends Controller {

    /**
     * Get list of all customers with optional filtering
     * @param active Filter by active status
     * @param storeId Filter by store
     */
    @Get()
    @SuccessResponse('200', 'Success')
    @SwaggerResponse('400', 'Bad Request')
    public async getCustomers(@Query() active?: boolean, @Query() storeId?: number): Promise<CustomerDto[]> {
        try {
            // Business logic to fetch customers
            return []; // Replace with actual data fetching logic
        } catch (error) {
            this.setStatus(400);
            throw new Error('Bad Request');
        }
    }

    /**
     * Get a single customer by ID
     * @param customerId Customer primary key
     */
    @Get('{customerId}')
    @SuccessResponse('200', 'Success')
    @SwaggerResponse('404', 'Customer not found')
    @SwaggerResponse('400', 'Invalid customer ID')
    public async getCustomer(@Path() customerId: number): Promise<CustomerDto> {
        try {
            if (customerId <= 0) {
                this.setStatus(400);
                throw new Error('Invalid customer ID');
            }
            // Business logic to fetch a single customer
            return {} as CustomerDto; // Replace with actual data fetching logic
        } catch (error) {
            this.setStatus(404);
            throw new Error('Customer not found');
        }
    }

    /**
     * Add a new customer
     * @param requestBody Customer data
     */
    @Post()
    @SuccessResponse('201', 'Created')
    @SwaggerResponse('400', 'Validation error')
    public async addCustomer(@Body() requestBody: CustomerDto): Promise<CustomerDto> {
        try {
            await validateOrReject(requestBody);
            // Business logic to add a new customer
            return requestBody; // Replace with actual data saving logic
        } catch (error) {
            this.setStatus(400);
            throw new Error('Validation error');
        }
    }

    /**
     * Update customer information
     * @param customerId Customer primary key
     * @param requestBody Updated customer data
     */
    @Put('{customerId}')
    @SuccessResponse('200', 'Success')
    @SwaggerResponse('404', 'Customer not found')
    @SwaggerResponse('400', 'Validation error')
    public async updateCustomer(@Path() customerId: number, @Body() requestBody: CustomerDto): Promise<CustomerDto> {
        try {
            if (customerId <= 0) {
                this.setStatus(400);
                throw new Error('Invalid customer ID');
            }
            await validateOrReject(requestBody);
            // Business logic to update customer
            return requestBody; // Replace with actual data updating logic
        } catch (error) {
            this.setStatus(404);
            throw new Error('Customer not found');
        }
    }

    /**
     * Delete a customer (soft delete by setting active=false)
     * @param customerId Customer primary key
     */
    @Delete('{customerId}')
    @SuccessResponse('204', 'No Content')
    @SwaggerResponse('404', 'Customer not found')
    @SwaggerResponse('409', 'Customer has open rentals')
    public async deleteCustomer(@Path() customerId: number): Promise<void> {
        try {
            if (customerId <= 0) {
                this.setStatus(400);
                throw new Error('Invalid customer ID');
            }
            // Business logic to soft delete customer
            this.setStatus(204);
        } catch (error) {
            this.setStatus(404);
            throw new Error('Customer not found');
        }
    }
}