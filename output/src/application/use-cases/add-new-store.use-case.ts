// StoreDto.ts
export interface StoreDto {
    id?: string;
    name: string;
    district: string;
    // other relevant fields
}

// IStoreRepository.ts
export interface IStoreRepository {
    addStore(store: StoreDto): Promise<void>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(): boolean;
    hasPermission(permission: string): boolean;
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

// AddNewStoreUseCase.ts
import { StoreDto } from './StoreDto';
import { IStoreRepository } from './IStoreRepository';
import { IAuthService } from './IAuthService';
import { Result } from './Result';

export class AddNewStoreUseCase {
    private storeRepository: IStoreRepository;
    private authService: IAuthService;

    constructor(storeRepository: IStoreRepository, authService: IAuthService) {
        this.storeRepository = storeRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to add a new store.
     * @param storeDto - The store details to be added.
     * @returns Result<void> - The result of the operation.
     */
    public async execute(storeDto: StoreDto): Promise<Result<void>> {
        if (!this.authService.isAuthenticated()) {
            return Result.fail('User is not authenticated.');
        }

        if (!this.authService.hasPermission('ADD_STORE')) {
            return Result.fail('User does not have permission to add stores.');
        }

        const validationError = this.validateStoreDto(storeDto);
        if (validationError) {
            return Result.fail(validationError);
        }

        try {
            await this.storeRepository.addStore(storeDto);
            return Result.ok(undefined);
        } catch (error) {
            return Result.fail(`Failed to add store: ${error.message}`);
        }
    }

    /**
     * Validates the store DTO.
     * @param storeDto - The store details to validate.
     * @returns string | undefined - Returns an error message if validation fails, otherwise undefined.
     */
    private validateStoreDto(storeDto: StoreDto): string | undefined {
        if (!storeDto.name || storeDto.name.trim().length === 0) {
            return 'Store name must not be empty.';
        }
        if (!storeDto.district || storeDto.district.trim().length < 1 || storeDto.district.trim().length > 20) {
            return 'District must not be null and must have valid size (1-20).';
        }
        // Additional validation rules can be added here
        return undefined;
    }
}