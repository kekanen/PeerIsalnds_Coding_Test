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

    public static ok<T>(value: T): Result<T> {
        return new Result<T>(true, value);
    }

    public static fail<T>(error: string): Result<T> {
        return new Result<T>(false, undefined, error);
    }
}

// SalesReportDto.ts
export interface SalesReportDto {
    storeId: string;
    totalSales: number;
    salesCount: number;
}

// ISalesRepository.ts
export interface ISalesRepository {
    getSalesByStore(storeId: string): Promise<SalesReportDto | null>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// ReportSalesByStoreUseCase.ts
import { Result } from './Result';
import { SalesReportDto } from './SalesReportDto';
import { ISalesRepository } from './ISalesRepository';
import { IAuthService } from './IAuthService';

interface ReportSalesByStoreInput {
    userId: string;
    storeId: string;
}

export class ReportSalesByStoreUseCase {
    private salesRepository: ISalesRepository;
    private authService: IAuthService;

    constructor(salesRepository: ISalesRepository, authService: IAuthService) {
        this.salesRepository = salesRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to report sales by store.
     * @param input - The input data for the use case.
     * @returns Result<SalesReportDto>
     */
    public async execute(input: ReportSalesByStoreInput): Promise<Result<SalesReportDto>> {
        const { userId, storeId } = input;

        // Validate preconditions
        if (!this.authService.isAuthenticated(userId)) {
            return Result.fail<SalesReportDto>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'view_sales_reports')) {
            return Result.fail<SalesReportDto>('User does not have permission to view sales reports.');
        }

        if (!storeId) {
            return Result.fail<SalesReportDto>('Store ID must not be null.');
        }

        try {
            // Retrieve sales data grouped by store
            const salesData = await this.salesRepository.getSalesByStore(storeId);

            if (!salesData) {
                return Result.fail<SalesReportDto>('No sales data found for the specified store.');
            }

            // Return the sales report
            return Result.ok<SalesReportDto>(salesData);
        } catch (error) {
            return Result.fail<SalesReportDto>('An error occurred while retrieving sales data: ' + error.message);
        }
    }
}