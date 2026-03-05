// FilmDto.ts
export interface FilmDto {
    id: string;
    title: string;
    description: string;
    replacementCost: number;
    lastUpdate: Date;
}

// IFilmRepository.ts
export interface IFilmRepository {
    updateFilm(film: FilmDto): Promise<void>;
    findFilmById(id: string): Promise<FilmDto | null>;
}

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

// UpdateFilmUseCase.ts
import { IFilmRepository } from './IFilmRepository';
import { FilmDto } from './FilmDto';
import { Result } from './Result';

export class UpdateFilmUseCase {
    private filmRepository: IFilmRepository;

    constructor(filmRepository: IFilmRepository) {
        this.filmRepository = filmRepository;
    }

    /**
     * Executes the use case to update film information.
     * @param filmDto The film data transfer object containing updated information.
     * @returns Result indicating success or failure.
     */
    public async execute(filmDto: FilmDto): Promise<Result<void>> {
        const validationResult = this.validate(filmDto);
        if (!validationResult.isSuccess) {
            return Result.fail(validationResult.error!);
        }

        try {
            const existingFilm = await this.filmRepository.findFilmById(filmDto.id);
            if (!existingFilm) {
                return Result.fail('Film not found.');
            }

            await this.filmRepository.updateFilm(filmDto);
            return Result.ok();
        } catch (error) {
            return Result.fail('An error occurred while updating the film information.');
        }
    }

    /**
     * Validates the film DTO according to business rules.
     * @param filmDto The film data transfer object to validate.
     * @returns Result indicating validation success or failure.
     */
    private validate(filmDto: FilmDto): Result<void> {
        if (!filmDto.id) {
            return Result.fail('Film ID must not be null.');
        }
        if (filmDto.replacementCost == null) {
            return Result.fail('Replacement cost must be specified.');
        }
        if (!filmDto.lastUpdate) {
            return Result.fail('Last update timestamp must not be null.');
        }
        return Result.ok();
    }
}