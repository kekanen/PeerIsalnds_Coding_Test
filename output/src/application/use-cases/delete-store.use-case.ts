// Result.ts
export class Result<T> {
    public isSuccess: boolean;
    public error: string | null;
    public value: T | null;

    private constructor(isSuccess: boolean, error: string | null, value: T | null) {
        this.isSuccess = isSuccess;
        this.error = error;
        this.value = value;
    }

    public static ok<T>(value: T): Result<T> {
        return new Result<T>(true, null, value);
    }

    public static fail<T>(error: string): Result<T> {
        return new Result<T>(false, error, null);
    }
}

// IStoreRepository.ts
export interface IStoreRepository {
    deleteStore(storeId: string): Promise<void>;
}

// IAuthorizationService.ts
export interface IAuthorizationService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// DeleteStoreRequestDto.ts
export class DeleteStoreRequestDto {
    constructor(public storeId: string) {}
}

// DeleteStoreResponseDto.ts
export class DeleteStoreResponseDto {
    constructor(public message: string) {}
}

// DeleteStoreUseCase.ts
import { IStoreRepository } from './IStoreRepository';
import { IAuthorizationService } from './IAuthorizationService';
import { Result } from './Result';
import { DeleteStoreRequestDto } from './DeleteStoreRequestDto';
import { DeleteStoreResponseDto } from './DeleteStoreResponseDto';

export class DeleteStoreUseCase {
    constructor(
        private storeRepository: IStoreRepository,
        private authorizationService: IAuthorizationService
    ) {}

    /**
     * Executes the delete store use case.
     * @param userId The ID of the user requesting the deletion.
     * @param request The request DTO containing the store ID.
     * @returns A Result containing the response DTO or an error message.
     */
    public async execute(userId: string, request: DeleteStoreRequestDto): Promise<Result<DeleteStoreResponseDto>> {
        // Validate preconditions
        if (!this.authorizationService.isAuthenticated(userId)) {
            return Result.fail<DeleteStoreResponseDto>('User is not authenticated.');
        }

        if (!this.authorizationService.hasPermission(userId, 'delete_store')) {
            return Result.fail<DeleteStoreResponseDto>('User does not have permission to delete stores.');
        }

        if (!request.storeId) {
            return Result.fail<DeleteStoreResponseDto>('Store ID must not be null.');
        }

        try {
            // Step 3: Delete the store from the database
            await this.storeRepository.deleteStore(request.storeId);
            return Result.ok(new DeleteStoreResponseDto('Store deleted successfully.'));
        } catch (error) {
            // Handle errors
            return Result.fail<DeleteStoreResponseDto>('An error occurred while deleting the store: ' + error.message);
        }
    }
}