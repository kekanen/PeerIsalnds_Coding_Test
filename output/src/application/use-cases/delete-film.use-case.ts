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

// IFilmRepository.ts
export interface IFilmRepository {
    deleteFilm(filmId: string): Promise<void>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// DeleteFilmRequestDto.ts
export class DeleteFilmRequestDto {
    constructor(public filmId: string) {}
}

// DeleteFilmResponseDto.ts
export class DeleteFilmResponseDto {
    constructor(public message: string) {}
}

// DeleteFilmUseCase.ts
import { IFilmRepository } from './IFilmRepository';
import { IAuthService } from './IAuthService';
import { DeleteFilmRequestDto } from './DeleteFilmRequestDto';
import { DeleteFilmResponseDto } from './DeleteFilmResponseDto';
import { Result } from './Result';

export class DeleteFilmUseCase {
    constructor(
        private filmRepository: IFilmRepository,
        private authService: IAuthService
    ) {}

    /**
     * Executes the use case to delete a film.
     * @param userId - ID of the user requesting the deletion.
     * @param requestDto - The request data transfer object containing film ID.
     * @returns Result<DeleteFilmResponseDto>
     */
    public async execute(userId: string, requestDto: DeleteFilmRequestDto): Promise<Result<DeleteFilmResponseDto>> {
        if (!this.authService.isAuthenticated(userId)) {
            return Result.failure<DeleteFilmResponseDto>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'delete_film')) {
            return Result.failure<DeleteFilmResponseDto>('User does not have permission to delete films.');
        }

        if (!requestDto.filmId) {
            return Result.failure<DeleteFilmResponseDto>('Film ID must not be null.');
        }

        try {
            await this.filmRepository.deleteFilm(requestDto.filmId);
            return Result.success(new DeleteFilmResponseDto('Film deleted successfully.'));
        } catch (error) {
            return Result.failure<DeleteFilmResponseDto>('An error occurred while deleting the film: ' + error.message);
        }
    }
}