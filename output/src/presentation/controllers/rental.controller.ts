import { Controller, Get, Post, Put, Route, Tags, Path, Body, Query, SuccessResponse, Response as SwaggerResponse } from 'tsoa';
import { Request, Response, NextFunction } from 'express';
import { validateOrReject } from 'class-validator';

/**
 * DTO for creating a rental
 */
class CreateRentalDto {
    inventoryId: number;
    customerId: number;
    staffId: number;
}

/**
 * DTO for returning a rental
 */
class ReturnRentalDto {
    rentalId: number;
}

/**
 * DTO for filtering rentals
 */
class GetRentalsQuery {
    customerId?: number;
    returned?: boolean;
}

/**
 * RentalController handles rental transactions
 */
@Route('rentals')
@Tags('Rentals')
export class RentalController extends Controller {
    constructor() {
        super();
    }

    /**
     * Get list of all rental transactions
     * @param customerId Optional filter by customer
     * @param returned Optional filter by return status
     */
    @Get()
    @SuccessResponse('200', 'Success')
    @SwaggerResponse('500', 'Internal Server Error')
    public async getRentals(@Query() query: GetRentalsQuery, req: Request, res: Response, next: NextFunction): Promise<void> {
        try {
            // Business logic to fetch rentals
            // const rentals = await rentalService.getRentals(query);
            res.status(200).json([]); // Replace with actual rentals
        } catch (error) {
            next(error);
        }
    }

    /**
     * Create a new rental (rent a DVD)
     * @param requestBody Rental creation details
     */
    @Post()
    @SuccessResponse('201', 'Created')
    @SwaggerResponse('400', 'Bad Request')
    @SwaggerResponse('403', 'Forbidden')
    public async createRental(@Body() requestBody: CreateRentalDto, req: Request, res: Response, next: NextFunction): Promise<void> {
        try {
            await validateOrReject(requestBody);
            // Business logic to create rental
            // const rental = await rentalService.createRental(requestBody);
            res.status(201).json({}); // Replace with actual rental response
        } catch (error) {
            next(error);
        }
    }

    /**
     * Return a rented DVD
     * @param rentalId Rental primary key
     */
    @Put('{rentalId}/return')
    @SuccessResponse('200', 'Returned')
    @SwaggerResponse('404', 'Not Found')
    @SwaggerResponse('409', 'Conflict')
    public async returnRental(@Path() rentalId: number, req: Request, res: Response, next: NextFunction): Promise<void> {
        try {
            if (rentalId <= 0) {
                throw new Error('Invalid rental ID');
            }
            // Business logic to return rental
            // await rentalService.returnRental(rentalId);
            res.status(200).json({}); // Replace with actual return response
        } catch (error) {
            next(error);
        }
    }
}