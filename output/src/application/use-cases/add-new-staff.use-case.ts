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

// StaffDto.ts
export interface StaffDto {
    username: string;
    authorityId: string;
    active: boolean;
}

// IStaffRepository.ts
export interface IStaffRepository {
    addStaff(staff: StaffDto): Promise<void>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(): boolean;
    hasPermission(permission: string): boolean;
}

// AddNewStaffUseCase.ts
import { Result } from './Result';
import { StaffDto } from './StaffDto';
import { IStaffRepository } from './IStaffRepository';
import { IAuthService } from './IAuthService';

export class AddNewStaffUseCase {
    private readonly staffRepository: IStaffRepository;
    private readonly authService: IAuthService;

    constructor(staffRepository: IStaffRepository, authService: IAuthService) {
        this.staffRepository = staffRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to add a new staff member.
     * @param staffDto The staff details to add.
     * @returns Result indicating success or failure.
     */
    public async execute(staffDto: StaffDto): Promise<Result<void>> {
        if (!this.authService.isAuthenticated()) {
            return Result.fail('User is not authenticated.');
        }

        if (!this.authService.hasPermission('add_staff')) {
            return Result.fail('User does not have permission to add staff.');
        }

        const validationError = this.validate(staffDto);
        if (validationError) {
            return Result.fail(validationError);
        }

        try {
            await this.staffRepository.addStaff(staffDto);
            return Result.ok<void>(undefined);
        } catch (error) {
            return Result.fail('Failed to add new staff member: ' + error.message);
        }
    }

    /**
     * Validates the staff data according to business rules.
     * @param staffDto The staff details to validate.
     * @returns A validation error message if invalid, otherwise undefined.
     */
    private validate(staffDto: StaffDto): string | undefined {
        if (!staffDto.username || staffDto.username.length < 1 || staffDto.username.length > 16) {
            return 'Username must be between 1 and 16 characters.';
        }

        if (!staffDto.authorityId) {
            return 'Authority ID must not be null.';
        }

        if (!staffDto.active) {
            return 'Active status must be true for staff.';
        }

        return undefined;
    }
}