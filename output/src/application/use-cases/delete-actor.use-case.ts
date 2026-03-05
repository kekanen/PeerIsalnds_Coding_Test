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

    public static success<T>(value: T): Result<T> {
        return new Result<T>(true, undefined, value);
    }

    public static failure<T>(error: string): Result<T> {
        return new Result<T>(false, error);
    }
}

// IActorRepository.ts
export interface IActorRepository {
    deleteActor(actorId: string): Promise<void>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// DeleteActorRequestDto.ts
export class DeleteActorRequestDto {
    constructor(public actorId: string) {}
}

// DeleteActorResponseDto.ts
export class DeleteActorResponseDto {
    constructor(public message: string) {}
}

// DeleteActorUseCase.ts
import { IActorRepository } from './IActorRepository';
import { IAuthService } from './IAuthService';
import { Result } from './Result';
import { DeleteActorRequestDto } from './DeleteActorRequestDto';
import { DeleteActorResponseDto } from './DeleteActorResponseDto';

export class DeleteActorUseCase {
    constructor(
        private actorRepository: IActorRepository,
        private authService: IAuthService,
        private userId: string
    ) {}

    /**
     * Executes the use case to delete an actor.
     * @param requestDto - The request data transfer object containing the actor ID.
     * @returns Result<DeleteActorResponseDto>
     */
    public async execute(requestDto: DeleteActorRequestDto): Promise<Result<DeleteActorResponseDto>> {
        // Validate preconditions
        if (!this.authService.isAuthenticated(this.userId)) {
            return Result.failure<DeleteActorResponseDto>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(this.userId, 'delete_actor')) {
            return Result.failure<DeleteActorResponseDto>('User does not have permission to delete actors.');
        }

        // Step 3: Attempt to delete the actor
        try {
            await this.actorRepository.deleteActor(requestDto.actorId);
            return Result.success(new DeleteActorResponseDto('Actor deleted successfully.'));
        } catch (error) {
            return Result.failure<DeleteActorResponseDto>('Failed to delete actor: ' + error.message);
        }
    }
}