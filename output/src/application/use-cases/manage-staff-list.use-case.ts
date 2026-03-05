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
    name: string;
    username: string;
    active: boolean;
}

// IStaffRepository.ts
export interface IStaffRepository {
    getAllStaff(): Promise<StaffDto[]>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// ManageStaffListUseCase.ts
import { Result } from './Result';
import { IStaffRepository } from './IStaffRepository';
import { IAuthService } from './IAuthService';
import { StaffDto } from './StaffDto';

/**
 * Use case for managing the staff list.
 */
export class ManageStaffListUseCase {
    private staffRepository: IStaffRepository;
    private authService: IAuthService;

    constructor(staffRepository: IStaffRepository, authService: IAuthService) {
        this.staffRepository = staffRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to retrieve the list of staff.
     * @param userId - The ID of the user requesting the staff list.
     * @returns Result containing the list of staff or an error message.
     */
    public async execute(userId: string): Promise<Result<StaffDto[]>> {
        // Validate preconditions
        if (!this.authService.isAuthenticated(userId)) {
            return Result.fail<StaffDto[]>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'manage_staff')) {
            return Result.fail<StaffDto[]>('User does not have permission to manage staff.');
        }

        try {
            // Step 2: System retrieves the list of staff
            const staffList = await this.staffRepository.getAllStaff();

            // Step 3: System displays the list to the user
            return Result.ok(staffList);
        } catch (error) {
            // Comprehensive error handling
            return Result.fail<StaffDto[]>('An error occurred while retrieving the staff list: ' + error.message);
        }
    }
}