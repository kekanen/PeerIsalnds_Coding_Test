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

// StoreDto.ts
export interface StoreDto {
    id: string;
    name: string;
    address: string;
    lastUpdated: Date;
}

// IStoreRepository.ts
export interface IStoreRepository {
    getAllStores(): Promise<StoreDto[]>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// ManageStoreListUseCase.ts
import { IStoreRepository } from './IStoreRepository';
import { IAuthService } from './IAuthService';
import { Result } from './Result';
import { StoreDto } from './StoreDto';

export class ManageStoreListUseCase {
    private storeRepository: IStoreRepository;
    private authService: IAuthService;

    constructor(storeRepository: IStoreRepository, authService: IAuthService) {
        this.storeRepository = storeRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to manage the store list.
     * @param userId - The ID of the user requesting the store list.
     * @returns Result containing the list of stores or an error message.
     */
    public async execute(userId: string): Promise<Result<StoreDto[]>> {
        if (!this.authService.isAuthenticated(userId)) {
            return Result.fail<StoreDto[]>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'manage_stores')) {
            return Result.fail<StoreDto[]>('User does not have permission to manage stores.');
        }

        try {
            const stores = await this.storeRepository.getAllStores();
            return Result.ok(stores);
        } catch (error) {
            return Result.fail<StoreDto[]>('An error occurred while retrieving the store list.');
        }
    }
}