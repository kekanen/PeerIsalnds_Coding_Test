// PaymentDto.ts
export interface PaymentDto {
    id: string;
    amount: number;
    date: Date;
    customerId: string;
}

// IPaymentRepository.ts
export interface IPaymentRepository {
    getAllPayments(): Promise<PaymentDto[]>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// Result.ts
export class Result<T> {
    public isSuccess: boolean;
    public error?: string;
    public value?: T;

    private constructor(isSuccess: boolean, error?: string, value?: T) {
        this.isSuccess = isSuccess;
        this.error = error;
        this.value = value;
    }

    public static ok<T>(value: T): Result<T> {
        return new Result<T>(true, undefined, value);
    }

    public static fail<T>(error: string): Result<T> {
        return new Result<T>(false, error);
    }
}

// ManagePaymentListUseCase.ts
import { IPaymentRepository } from './IPaymentRepository';
import { IAuthService } from './IAuthService';
import { PaymentDto } from './PaymentDto';
import { Result } from './Result';

export class ManagePaymentListUseCase {
    private readonly paymentRepository: IPaymentRepository;
    private readonly authService: IAuthService;

    constructor(paymentRepository: IPaymentRepository, authService: IAuthService) {
        this.paymentRepository = paymentRepository;
        this.authService = authService;
    }

    /**
     * Execute the use case to manage the list of payments.
     * @param userId - The ID of the staff member requesting the payment list.
     * @returns Result<PaymentDto[]> - The result containing the list of payments or an error message.
     */
    public async execute(userId: string): Promise<Result<PaymentDto[]>> {
        // Validate preconditions
        if (!this.authService.isAuthenticated(userId)) {
            return Result.fail<PaymentDto[]>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'manage_payments')) {
            return Result.fail<PaymentDto[]>('User does not have permission to manage payments.');
        }

        try {
            // Step 2: Retrieve the list of payments
            const payments = await this.paymentRepository.getAllPayments();

            // Step 3: Return the list to the user
            return Result.ok(payments);
        } catch (error) {
            // Comprehensive error handling
            return Result.fail<PaymentDto[]>('An error occurred while retrieving the payment list: ' + error.message);
        }
    }
}