// StoreDto.ts
export interface StoreDto {
    id: string;
    name: string;
    address: string;
    lastUpdated: Date;
}

// IStoreRepository.ts
export interface IStoreRepository {
    updateStore(store: StoreDto): Promise<void>;
    findStoreById(id: string): Promise<StoreDto | null>;
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

    public static ok<T>(value?: T): Result<T> {
        return new Result<T>(true, undefined, value);
    }

    public static fail<T>(error: string): Result<T> {
        return new Result<T>(false, error);
    }
}

// UpdateStoreInformationUseCase.ts
import { IStoreRepository } from './IStoreRepository';
import { StoreDto } from './StoreDto';
import { Result } from './Result';

export class UpdateStoreInformationUseCase {
    private storeRepository: IStoreRepository;

    constructor(storeRepository: IStoreRepository) {
        this.storeRepository = storeRepository;
    }

    /**
     * Executes the use case to update store information.
     * @param storeDto - The store data transfer object containing updated information.
     * @returns Result indicating success or failure.
     */
    public async execute(storeDto: StoreDto): Promise<Result<void>> {
        const validationResult = this.validate(storeDto);
        if (!validationResult.isSuccess) {
            return Result.fail(validationResult.error);
        }

        const existingStore = await this.storeRepository.findStoreById(storeDto.id);
        if (!existingStore) {
            return Result.fail('Store not found');
        }

        try {
            await this.storeRepository.updateStore({
                ...existingStore,
                ...storeDto,
                lastUpdated: new Date() // Enforcing last update timestamp
            });
            return Result.ok();
        } catch (error) {
            return Result.fail('Failed to update store information');
        }
    }

    /**
     * Validates the store DTO.
     * @param storeDto - The store data transfer object to validate.
     * @returns Result indicating validation success or failure.
     */
    private validate(storeDto: StoreDto): Result<void> {
        if (!storeDto.id) {
            return Result.fail('Store ID must not be null');
        }
        if (!storeDto.lastUpdated) {
            return Result.fail('Last update timestamp must not be null');
        }
        // Additional validation rules can be added here
        return Result.ok();
    }
}