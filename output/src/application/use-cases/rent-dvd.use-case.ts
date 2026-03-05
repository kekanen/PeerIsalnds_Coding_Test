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
    isDvdAvailable(dvdId: string): Promise<boolean>;
    rentDvd(dvdId: string, customerId: string): Promise<void>;
}

// IUserService.ts
export interface IUserService {
    isAuthenticated(userId: string): boolean;
}

// RentDvdDto.ts
export interface RentDvdDto {
    dvdId: string;
    customerId: string;
}

// RentDvdResponseDto.ts
export interface RentDvdResponseDto {
    message: string;
}

// RentDvdUseCase.ts
import { IDvdRepository } from './IDvdRepository';
import { IUserService } from './IUserService';
import { RentDvdDto } from './RentDvdDto';
import { RentDvdResponseDto } from './RentDvdResponseDto';
import { Result } from './Result';

export class RentDvdUseCase {
    private dvdRepository: IDvdRepository;
    private userService: IUserService;

    constructor(dvdRepository: IDvdRepository, userService: IUserService) {
        this.dvdRepository = dvdRepository;
        this.userService = userService;
    }

    /**
     * Executes the DVD rental process.
     * @param dto - The rental DTO containing DVD and customer information.
     * @returns Result<RentDvdResponseDto>
     */
    public async execute(dto: RentDvdDto): Promise<Result<RentDvdResponseDto>> {
        // Validate preconditions
        if (!this.userService.isAuthenticated(dto.customerId)) {
            return Result.fail<RentDvdResponseDto>('User is not authenticated.');
        }

        const isAvailable = await this.dvdRepository.isDvdAvailable(dto.dvdId);
        if (!isAvailable) {
            return Result.fail<RentDvdResponseDto>('DVD is not available for rent.');
        }

        // Execute business logic
        try {
            await this.dvdRepository.rentDvd(dto.dvdId, dto.customerId);
            return Result.ok<RentDvdResponseDto>({ message: 'DVD rented successfully.' });
        } catch (error) {
            return Result.fail<RentDvdResponseDto>('Failed to rent DVD: ' + error.message);
        }
    }
}