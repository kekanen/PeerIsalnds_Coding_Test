// Result.ts
export class Result<T> {
    public isSuccess: boolean;
    public error?: string;
    public value?: T;

    private constructor(isSuccess: boolean, value?: T, error?: string) {
        this.isSuccess = isSuccess;
        this.value = value;
        this.error = error;
    }

    public static ok<T>(value?: T): Result<T> {
        return new Result<T>(true, value);
    }

    public static fail<T>(error: string): Result<T> {
        return new Result<T>(false, undefined, error);
    }
}

// IDvdRepository.ts
export interface IDvdRepository {
    findRentalByCustomerId(customerId: string, dvdId: string): Promise<RentalDto | null>;
    updateRentalStatus(rentalId: string, status: string): Promise<void>;
}

// RentalDto.ts
export class RentalDto {
    constructor(public rentalId: string, public customerId: string, public dvdId: string, public status: string) {}
}

// ReturnDvdUseCase.ts
import { IDvdRepository } from './IDvdRepository';
import { Result } from './Result';
import { RentalDto } from './RentalDto';

/**
 * Use case for returning a DVD.
 */
export class ReturnDvdUseCase {
    constructor(private dvdRepository: IDvdRepository) {}

    /**
     * Executes the return DVD use case.
     * @param customerId The ID of the customer returning the DVD.
     * @param dvdId The ID of the DVD being returned.
     * @returns Result indicating success or failure.
     */
    public async execute(customerId: string, dvdId: string): Promise<Result<void>> {
        if (!customerId) {
            return Result.fail('User must be authenticated.');
        }

        const rental = await this.dvdRepository.findRentalByCustomerId(customerId, dvdId);
        if (!rental) {
            return Result.fail('No rental record found for this DVD and customer.');
        }

        if (rental.status !== 'Rented') {
            return Result.fail('DVD is not currently rented.');
        }

        try {
            await this.dvdRepository.updateRentalStatus(rental.rentalId, 'Returned');
            return Result.ok();
        } catch (error) {
            return Result.fail('Failed to update rental status: ' + error.message);
        }
    }
}