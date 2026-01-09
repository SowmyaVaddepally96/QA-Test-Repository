package com.babyshop.catalog;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Long> {

    @Query("""
            select p from Product p
            where lower(p.name) like lower(concat('%', :q, '%'))
               or lower(p.description) like lower(concat('%', :q, '%'))
            order by p.name asc
            """)
    List<Product> search(@Param("q") String q);

    List<Product> findAllByOrderByNameAsc();
}

