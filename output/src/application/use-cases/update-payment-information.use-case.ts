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

// PaymentInfoDto.ts
export interface PaymentInfoDto {
    cardNumber: string;
    expirationDate: string;
    cvv: string;
}

// IPaymentRepository.ts
export interface IPaymentRepository {
    updatePaymentInfo(userId: string, paymentInfo: PaymentInfoDto): Promise<void>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// UpdatePaymentInfoUseCase.ts
import { Result } from './Result';
import { PaymentInfoDto } from './PaymentInfoDto';
import { IPaymentRepository } from './IPaymentRepository';
import { IAuthService } from './IAuthService';

export class UpdatePaymentInfoUseCase {
    private paymentRepository: IPaymentRepository;
    private authService: IAuthService;

    constructor(paymentRepository: IPaymentRepository, authService: IAuthService) {
        this.paymentRepository = paymentRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to update payment information.
     * @param userId - The ID of the authenticated user.
     * @param paymentInfo - The updated payment information.
     * @returns Result<void>
     */
    public async execute(userId: string, paymentInfo: PaymentInfoDto): Promise<Result<void>> {
        if (!this.authService.isAuthenticated(userId)) {
            return Result.fail('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'update_payments')) {
            return Result.fail('User does not have permission to update payment information.');
        }

        const validationErrors = this.validatePaymentInfo(paymentInfo);
        if (validationErrors.length > 0) {
            return Result.fail(`Validation errors: ${validationErrors.join(', ')}`);
        }

        try {
            await this.paymentRepository.updatePaymentInfo(userId, paymentInfo);
            return Result.ok();
        } catch (error) {
            return Result.fail(`Failed to update payment information: ${error.message}`);
        }
    }

    /**
     * Validates the payment information.
     * @param paymentInfo - The payment information to validate.
     * @returns string[]
     */
    private validatePaymentInfo(paymentInfo: PaymentInfoDto): string[] {
        const errors: string[] = [];
        if (!paymentInfo.cardNumber) {
            errors.push('Card number is required.');
        }
        if (!paymentInfo.expirationDate) {
            errors.push('Expiration date is required.');
        }
        if (!paymentInfo.cvv) {
            errors.push('CVV is required.');
        }
        // Additional validation rules can be added here
        return errors;
    }
}