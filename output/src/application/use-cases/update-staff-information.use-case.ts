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

// StaffDto.ts
export interface StaffDto {
    id: string;
    username: string;
    authorityId: string;
    lastUpdated: Date;
}

// IStaffRepository.ts
export interface IStaffRepository {
    updateStaff(staff: StaffDto): Promise<void>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(): boolean;
    hasPermission(permission: string): boolean;
}

// UpdateStaffInformationUseCase.ts
import { Result } from './Result';
import { StaffDto } from './StaffDto';
import { IStaffRepository } from './IStaffRepository';
import { IAuthService } from './IAuthService';

/**
 * Use case for updating staff information.
 */
export class UpdateStaffInformationUseCase {
    private staffRepository: IStaffRepository;
    private authService: IAuthService;

    constructor(staffRepository: IStaffRepository, authService: IAuthService) {
        this.staffRepository = staffRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to update staff information.
     * @param staffDto The staff data transfer object containing updated information.
     * @returns Result indicating success or failure.
     */
    public async execute(staffDto: StaffDto): Promise<Result<void>> {
        // Validate preconditions
        if (!this.authService.isAuthenticated()) {
            return Result.fail('User is not authenticated.');
        }
        if (!this.authService.hasPermission('update_staff')) {
            return Result.fail('User does not have permission to update staff.');
        }

        // Validate business rules
        if (!staffDto.authorityId) {
            return Result.fail('Authority ID must not be null.');
        }
        if (staffDto.username.length < 1 || staffDto.username.length > 16) {
            return Result.fail('Username must be between 1 and 16 characters.');
        }
        if (!staffDto.lastUpdated) {
            return Result.fail('Last update timestamp must not be null.');
        }

        try {
            // Update staff information in the database
            await this.staffRepository.updateStaff(staffDto);
            return Result.ok();
        } catch (error) {
            return Result.fail(`Failed to update staff information: ${error.message}`);
        }
    }
}