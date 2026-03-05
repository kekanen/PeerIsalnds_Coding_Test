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

    public static success<T>(value: T): Result<T> {
        return new Result<T>(true, value);
    }

    public static failure<T>(error: string): Result<T> {
        return new Result<T>(false, undefined, error);
    }
}

// ICustomerRepository.ts
export interface ICustomerRepository {
    deleteCustomer(customerId: string): Promise<void>;
    findCustomerById(customerId: string): Promise<Customer | null>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// DeleteCustomerRequestDto.ts
export class DeleteCustomerRequestDto {
    constructor(public customerId: string) {}
}

// DeleteCustomerResponseDto.ts
export class DeleteCustomerResponseDto {
    constructor(public message: string) {}
}

// DeleteCustomerUseCase.ts
import { ICustomerRepository } from './ICustomerRepository';
import { IAuthService } from './IAuthService';
import { Result } from './Result';
import { DeleteCustomerRequestDto } from './DeleteCustomerRequestDto';
import { DeleteCustomerResponseDto } from './DeleteCustomerResponseDto';

export class DeleteCustomerUseCase {
    constructor(
        private customerRepository: ICustomerRepository,
        private authService: IAuthService
    ) {}

    /**
     * Execute the use case to delete a customer.
     * @param userId - The ID of the staff member requesting the deletion.
     * @param requestDto - The request data transfer object containing customer ID.
     * @returns Result<DeleteCustomerResponseDto>
     */
    public async execute(userId: string, requestDto: DeleteCustomerRequestDto): Promise<Result<DeleteCustomerResponseDto>> {
        if (!this.authService.isAuthenticated(userId)) {
            return Result.failure<DeleteCustomerResponseDto>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'delete_customer')) {
            return Result.failure<DeleteCustomerResponseDto>('User does not have permission to delete customers.');
        }

        const customerId = requestDto.customerId;

        if (!customerId) {
            return Result.failure<DeleteCustomerResponseDto>('Customer ID must not be null.');
        }

        const customer = await this.customerRepository.findCustomerById(customerId);
        if (!customer) {
            return Result.failure<DeleteCustomerResponseDto>('Customer not found.');
        }

        try {
            await this.customerRepository.deleteCustomer(customerId);
            return Result.success(new DeleteCustomerResponseDto('Customer deleted successfully.'));
        } catch (error) {
            return Result.failure<DeleteCustomerResponseDto>('An error occurred while deleting the customer.');
        }
    }
}