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

// CustomerDto.ts
export interface CustomerDto {
    username: string;
    authorityId: string;
    isActive: boolean;
}

// ICustomerRepository.ts
export interface ICustomerRepository {
    addCustomer(customer: CustomerDto): Promise<void>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(): boolean;
    hasPermission(permission: string): boolean;
}

// AddNewCustomerUseCase.ts
import { Result } from './Result';
import { CustomerDto } from './CustomerDto';
import { ICustomerRepository } from './ICustomerRepository';
import { IAuthService } from './IAuthService';

export class AddNewCustomerUseCase {
    private customerRepository: ICustomerRepository;
    private authService: IAuthService;

    constructor(customerRepository: ICustomerRepository, authService: IAuthService) {
        this.customerRepository = customerRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to add a new customer.
     * @param customerDto - The customer data to be added.
     * @returns Result indicating success or failure.
     */
    public async execute(customerDto: CustomerDto): Promise<Result<void>> {
        if (!this.authService.isAuthenticated()) {
            return Result.fail('User is not authenticated.');
        }

        if (!this.authService.hasPermission('ADD_CUSTOMER')) {
            return Result.fail('User does not have permission to add customers.');
        }

        const validationError = this.validate(customerDto);
        if (validationError) {
            return Result.fail(validationError);
        }

        try {
            await this.customerRepository.addCustomer(customerDto);
            return Result.ok();
        } catch (error) {
            return Result.fail('Failed to add new customer: ' + error.message);
        }
    }

    /**
     * Validates the customer data.
     * @param customerDto - The customer data to validate.
     * @returns A string error message if validation fails, otherwise undefined.
     */
    private validate(customerDto: CustomerDto): string | undefined {
        if (customerDto.username.length < 1 || customerDto.username.length > 16) {
            return 'Username must be between 1 and 16 characters.';
        }

        if (!customerDto.authorityId) {
            return 'Authority ID must not be null.';
        }

        if (!customerDto.isActive) {
            return 'Active status must be true for customers.';
        }

        return undefined;
    }
}