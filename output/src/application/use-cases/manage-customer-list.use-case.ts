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
    id: string;
    name: string;
    email: string;
    isActive: boolean;
}

// ICustomerRepository.ts
export interface ICustomerRepository {
    getAllCustomers(): Promise<CustomerDto[]>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// ManageCustomerListUseCase.ts
import { Result } from './Result';
import { CustomerDto } from './CustomerDto';
import { ICustomerRepository } from './ICustomerRepository';
import { IAuthService } from './IAuthService';

export class ManageCustomerListUseCase {
    private customerRepository: ICustomerRepository;
    private authService: IAuthService;

    constructor(customerRepository: ICustomerRepository, authService: IAuthService) {
        this.customerRepository = customerRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to manage the customer list.
     * @param userId - The ID of the user requesting the customer list.
     * @returns Result<CustomerDto[]> - The result containing the list of customers or an error.
     */
    public async execute(userId: string): Promise<Result<CustomerDto[]>> {
        if (!this.authService.isAuthenticated(userId)) {
            return Result.fail<CustomerDto[]>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'manage_customers')) {
            return Result.fail<CustomerDto[]>('User does not have permission to manage customers.');
        }

        try {
            const customers = await this.customerRepository.getAllCustomers();
            const activeCustomers = customers.filter(customer => customer.isActive);
            return Result.ok(activeCustomers);
        } catch (error) {
            return Result.fail<CustomerDto[]>('Failed to retrieve customer list: ' + error.message);
        }
    }
}