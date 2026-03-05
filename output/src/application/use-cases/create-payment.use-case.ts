// PaymentDto.ts
export interface PaymentDto {
  amount: number;
  paymentMethod: string;
  transactionId: string;
}

// PaymentResponseDto.ts
export interface PaymentResponseDto {
  success: boolean;
  message: string;
  paymentId?: string;
}

// IPaymentRepository.ts
export interface IPaymentRepository {
  createPayment(paymentDto: PaymentDto): Promise<string>;
}

// IAuthService.ts
export interface IAuthService {
  isAuthenticated(userId: string): boolean;
}

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

// CreatePaymentUseCase.ts
import { PaymentDto, PaymentResponseDto } from './PaymentDto';
import { IPaymentRepository } from './IPaymentRepository';
import { IAuthService } from './IAuthService';
import { Result } from './Result';

export class CreatePaymentUseCase {
  constructor(
    private paymentRepository: IPaymentRepository,
    private authService: IAuthService
  ) {}

  /**
   * Executes the payment creation process.
   * @param userId - The ID of the user making the payment.
   * @param paymentDto - The payment details.
   * @returns A Result containing the payment response.
   */
  public async execute(userId: string, paymentDto: PaymentDto): Promise<Result<PaymentResponseDto>> {
    // Validate preconditions
    if (!this.authService.isAuthenticated(userId)) {
      return Result.fail<PaymentResponseDto>('User is not authenticated.');
    }

    if (!this.validatePaymentDetails(paymentDto)) {
      return Result.fail<PaymentResponseDto>('Invalid payment details.');
    }

    try {
      // Step 1: Record the payment transaction
      const paymentId = await this.paymentRepository.createPayment(paymentDto);
      return Result.ok<PaymentResponseDto>({
        success: true,
        message: 'Payment created successfully.',
        paymentId: paymentId,
      });
    } catch (error) {
      return Result.fail<PaymentResponseDto>('Failed to create payment: ' + error.message);
    }
  }

  /**
   * Validates the payment details.
   * @param paymentDto - The payment details to validate.
   * @returns A boolean indicating if the details are valid.
   */
  private validatePaymentDetails(paymentDto: PaymentDto): boolean {
    return paymentDto.amount > 0 && !!paymentDto.paymentMethod && !!paymentDto.transactionId;
  }
}