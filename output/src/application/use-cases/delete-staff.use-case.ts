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

// IStaffRepository.ts
export interface IStaffRepository {
    deleteStaff(staffId: string): Promise<void>;
    findStaffById(staffId: string): Promise<StaffEntity | null>;
}

// StaffEntity.ts
export class StaffEntity {
    constructor(
        public id: string,
        public username: string,
        public isActive: boolean,
        public authorityId: string | null
    ) {}
}

// DeleteStaffRequestDto.ts
export class DeleteStaffRequestDto {
    constructor(public staffId: string) {}
}

// DeleteStaffResponseDto.ts
export class DeleteStaffResponseDto {
    constructor(public message: string) {}
}

// DeleteStaffUseCase.ts
import { IStaffRepository } from './IStaffRepository';
import { Result } from './Result';
import { DeleteStaffRequestDto } from './DeleteStaffRequestDto';
import { DeleteStaffResponseDto } from './DeleteStaffResponseDto';
import { StaffEntity } from './StaffEntity';

export class DeleteStaffUseCase {
    constructor(private staffRepository: IStaffRepository) {}

    /**
     * Executes the use case for deleting a staff member.
     * @param requestDto - The request data transfer object containing staff ID.
     * @returns Result<DeleteStaffResponseDto>
     */
    public async execute(requestDto: DeleteStaffRequestDto): Promise<Result<DeleteStaffResponseDto>> {
        const validationResult = this.validate(requestDto);
        if (!validationResult.isSuccess) {
            return Result.fail(validationResult.error);
        }

        const staff = await this.staffRepository.findStaffById(requestDto.staffId);
        if (!staff) {
            return Result.fail('Staff member not found.');
        }

        if (!staff.isActive) {
            return Result.fail('Cannot delete inactive staff member.');
        }

        if (!staff.authorityId) {
            return Result.fail('Authority ID must not be null.');
        }

        try {
            await this.staffRepository.deleteStaff(requestDto.staffId);
            return Result.ok(new DeleteStaffResponseDto('Staff member deleted successfully.'));
        } catch (error) {
            return Result.fail('An error occurred while deleting the staff member.');
        }
    }

    /**
     * Validates the request DTO.
     * @param requestDto - The request data transfer object.
     * @returns Result<void>
     */
    private validate(requestDto: DeleteStaffRequestDto): Result<void> {
        if (!requestDto.staffId) {
            return Result.fail('Staff ID must not be empty.');
        }
        return Result.ok();
    }
}