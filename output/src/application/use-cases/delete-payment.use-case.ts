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

// DeletePaymentRequestDto.ts
export interface DeletePaymentRequestDto {
    paymentId: string;
}

// IPaymentRepository.ts
export interface IPaymentRepository {
    delete(paymentId: string): Promise<void>;
}

// IUserService.ts
export interface IUserService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// DeletePaymentUseCase.ts
import { Result } from './Result';
import { DeletePaymentRequestDto } from './DeletePaymentRequestDto';
import { IPaymentRepository } from './IPaymentRepository';
import { IUserService } from './IUserService';

/**
 * Use case for deleting a payment.
 */
export class DeletePaymentUseCase {
    private paymentRepository: IPaymentRepository;
    private userService: IUserService;

    constructor(paymentRepository: IPaymentRepository, userService: IUserService) {
        this.paymentRepository = paymentRepository;
        this.userService = userService;
    }

    /**
     * Executes the use case to delete a payment.
     * @param userId - The ID of the user requesting the deletion.
     * @param request - The request data containing paymentId.
     * @returns Result indicating success or failure.
     */
    public async execute(userId: string, request: DeletePaymentRequestDto): Promise<Result<void>> {
        // Validate preconditions
        if (!this.userService.isAuthenticated(userId)) {
            return Result.fail('User is not authenticated.');
        }

        if (!this.userService.hasPermission(userId, 'delete_payments')) {
            return Result.fail('User does not have permission to delete payments.');
        }

        // Step 3: System deletes the payment from the database
        try {
            await this.paymentRepository.delete(request.paymentId);
            return Result.ok();
        } catch (error) {
            return Result.fail(`Failed to delete payment: ${error.message}`);
        }
    }
}